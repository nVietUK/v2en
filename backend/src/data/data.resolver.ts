import { Args, Mutation, Query, Resolver, Subscription } from '@nestjs/graphql';
import { NewDataInput } from './dto/data.args';
import { DataService } from './data.service';
import { NotFoundException } from '@nestjs/common';
import { Data } from './data.entity';
import { PubSub } from 'graphql-subscriptions';

const pubSub = new PubSub();

@Resolver(() => Data)
export class DataResolver {
	constructor(private readonly dataService: DataService) {}

	@Query(() => Data)
	async data(@Args('id') id: number): Promise<Data> {
		const data = await this.dataService.findOneBy({
			id: id,
		});
		if (!data) {
			throw new NotFoundException(id);
		}
		return data;
	}

	@Query(() => [Data])
	datas(): Promise<Data[]> {
		return this.dataService.findAll();
	}

	@Mutation(() => Data)
	async addData(
		@Args('newDataInput') newDataInput: NewDataInput,
	): Promise<Data> {
		const data = await this.dataService.create(
			new NewDataInput(
				newDataInput.origin,
				newDataInput.translated,
				newDataInput.translator,
				newDataInput.verified,
			),
		);

		pubSub.publish('dataAdded', { dataAdded: data });
		return data;
	}

	@Subscription(() => Data)
	dataAdded() {
		return pubSub.asyncIterator('dataAdded');
	}
}

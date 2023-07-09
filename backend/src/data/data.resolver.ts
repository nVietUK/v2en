import { Args, Mutation, Query, Resolver, Subscription } from '@nestjs/graphql';
import { DataService } from './data.service';
import { NotFoundException } from '@nestjs/common';
import { Data } from './data.entity';
import { PubSub } from 'graphql-subscriptions';
import { DataInput } from './data.dto';

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
	async addData(@Args('newData') newData: DataInput): Promise<Data> {
		const data = await this.dataService.createData(newData);

		pubSub.publish('dataAdded', { dataAdded: data });
		return data;
	}

	@Subscription(() => Data)
	dataAdded() {
		return pubSub.asyncIterator('dataAdded');
	}
}

import { Args, Mutation, Query, Resolver, Subscription } from '@nestjs/graphql';
import { DataService } from './data.service';
import { NotFoundException } from '@nestjs/common';
import { Data } from './data.entity';
import { PubSub } from 'graphql-subscriptions';
import { DataInput } from './data.dto';
import { GraphQLError } from 'graphql';

const pubSub = new PubSub();

@Resolver(() => Data)
export class DataResolver {
	constructor(private readonly dataService: DataService) {}

	// Queries:Section: Data
	@Query(() => [Data])
	datas(): Promise<Data[]> {
		return this.dataService.findDataAll();
	}

	// Mutations:Section: Data
	@Mutation(() => Data)
	async addData(
		@Args('newData') newData: DataInput,
	): Promise<Data | unknown> {
		let data = await Data.fromDataInput(newData);
		if (
			(await this.dataService.findDataOneBy({
				hashValue: data.hashValue,
			})) instanceof Error
		) {
			data = await this.dataService.createData(data);
			pubSub.publish('dataAdded', { dataAdded: data });
			return data;
		}
		return new GraphQLError('Data already existed');
	}

	@Mutation(() => String)
	async removeData(@Args('id') id: number) {
		const data = await this.dataService.findDataOneBy({ id: id });
		if (data instanceof Data) {
			this.dataService.removeData({ hashValue: data.hashValue });
			return 'Data removed';
		} else return new GraphQLError("Data isn't existed");
	}

	@Mutation(() => String)
	async modifyData(
		@Args('id') id: number,
		@Args('newData') newData: DataInput,
	) {
		this.removeData(id);
		this.addData(newData);
		return 'Data modified';
	}
}

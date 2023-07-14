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
	constructor(private readonly dataService: DataService) { }

	// Queries:Section: Data
	@Query(() => [Data])
	datas(): Promise<Data[]> {
		return this.dataService.findDataAll();
	}

	// Mutations:Section: Data
	@Mutation(() => Data)
	async addData(@Args('newData') newData: DataInput,): Promise<Data | unknown> {
		try {
			let data = await Data.fromDataInput(newData);
			if (await this.dataService.findDataOneBy({ hashValue: data.hashValue }) instanceof Error) {
				data = await this.dataService.createData(data);
				pubSub.publish('dataAdded', { dataAdded: data });
				return data;
			}
			return new GraphQLError('Data already existed');
		} catch (e) {
			return e;
		}
	}
}
